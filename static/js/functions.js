const submit = () => {
    // get every xpath value
    let url = $('input[name=url]').val()
    const hostname = new URL(url).hostname

    let all_links = $('input[name=all_links_xp]').val()
    let content = $('input[name=content_xp]').val()
    let all_subs = $('input[name=all_subs_xp]').val()
    let images = $('input[name=images_xp]').val()
    let videos = $('input[name=videos_xp]').val()
    let share_content = $('input[name=share_content_xp]').val()
    let tag = $('input[name=tag_xp]').val()
    let author = $('input[name=author_xp]').val()
    let raw_html = $('input[name=raw_html_xp]').val()
    let published_time = $('input[name=published_time_xp]').val()

    let payload = {
        url: url,
        all_links: all_links,
        all_subs: all_subs,
        content: content,
        next_page: '',
        image_sources: images,
        video_sources: videos,
        author_display_name: author,
        tags: tag,
        published_time: published_time,
        share_content: share_content,
        raw_html: raw_html
    }

    if (!check_valid_params(all_links, all_subs, content, images, author, raw_html)) {
        alert("All required fields must be filled")
    } else {
        fetch(`${window.origin}/submit`, {
            method: 'POST',
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json'
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(payload)
        })
            .then(async (res) => {
                const response = await res.text()
                if (response === "success") {
                    alert(hostname + " submission success")
                } else {
                    alert(hostname + " submission FAILED")
                }
            })
            .catch(e => console.log("Error: " + e))
    }
}

const check_valid_params =(a, b, c, d, e, f) => a !== '' && b !== '' && c !== '' && d !== '' && e !== '' && f !== ''

const check_existed_domain = () => {
    let url = $('input[name=url]').val()
    const hostname = new URL(url).hostname

    fetch(`${window.origin}/check_existed_domain`, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({ domain: hostname })
    })
        .then(async (res) => {
            const response = await res.text()
            if (response === "existed") {
                alert(hostname + " existed")
            } else {
                alert(hostname + " NOT existed")
            }
        })
        .catch(e => console.log("Error: " + e))
}